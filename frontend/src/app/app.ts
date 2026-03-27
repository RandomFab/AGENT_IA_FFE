import { Component } from '@angular/core';
import { Chessboard } from './components/chessboard/chessboard';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [Chessboard], // 👈 ajoute ça
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class AppComponent {}