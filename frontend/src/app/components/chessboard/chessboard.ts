import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Chess, Square } from 'chess.js';

interface BoardSquare {
  square: Square;
  piece: { type: string; color: string } | null;
  isLight: boolean;
  isSelected: boolean;
  isLegalMove: boolean;
}

@Component({
  selector: 'app-chessboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './chessboard.html',
  styleUrl: './chessboard.scss'
})
export class Chessboard implements OnInit {
  @Output() fenChange = new EventEmitter<string>();

  chess = new Chess();
  board: BoardSquare[][] = [];
  selectedSquare: Square | null = null;
  legalMoves: Square[] = [];
  draggedFrom: Square | null = null;

  pieceUnicode: Record<string, string> = {
    wk: '♔', wq: '♕', wr: '♖', wb: '♗', wn: '♘', wp: '♙',
    bk: '♚', bq: '♛', br: '♜', bb: '♝', bn: '♞', bp: '♟',
  };

  ngOnInit() {
    this.updateBoard();
  }

  updateBoard() {
    const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
    this.board = [];
    for (let rank = 8; rank >= 1; rank--) {
      const row: BoardSquare[] = [];
      for (let f = 0; f < 8; f++) {
        const square = `${files[f]}${rank}` as Square;
        const piece = this.chess.get(square);
        row.push({
          square,
          piece: piece || null,
          isLight: (f + rank) % 2 !== 0,
          isSelected: this.selectedSquare === square,
          isLegalMove: this.legalMoves.includes(square),
        });
      }
      this.board.push(row);
    }
  }

  getPieceSymbol(piece: { type: string; color: string } | null): string {
    if (!piece) return '';
    return this.pieceUnicode[piece.color + piece.type] ?? '';
  }

  onDragStart(event: DragEvent, square: Square) {
    const piece = this.chess.get(square);
    if (!piece || piece.color !== this.chess.turn()) {
      event.preventDefault();
      return;
    }
    this.draggedFrom = square;
    this.selectedSquare = square;
    this.legalMoves = this.chess.moves({ square, verbose: true }).map(m => m.to as Square);
    this.updateBoard();
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
  }

  onDrop(event: DragEvent, toSquare: Square) {
    event.preventDefault();
    if (!this.draggedFrom) return;
    this.tryMove(this.draggedFrom, toSquare);
    this.draggedFrom = null;
  }

  tryMove(from: Square, to: Square) {
    try {
      const move = this.chess.move({ from, to, promotion: 'q' });
      if (move) {
        this.selectedSquare = null;
        this.legalMoves = [];
        this.updateBoard();
        this.fenChange.emit(this.chess.fen());
      }
    } catch {
      this.selectedSquare = null;
      this.legalMoves = [];
      this.updateBoard();
    }
  }

  getFen(): string {
    return this.chess.fen();
  }

  reset() {
    this.chess.reset();
    this.selectedSquare = null;
    this.legalMoves = [];
    this.updateBoard();
    this.fenChange.emit(this.chess.fen());
  }
}