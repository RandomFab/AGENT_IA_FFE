import { Component, inject, ViewChild } from '@angular/core';
import { Chessboard } from './components/chessboard/chessboard';
import { RecommendationPanel } from "./components/recommendation-panel/recommendation-panel";
import { AgentService } from './services/agent.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [Chessboard, RecommendationPanel],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class AppComponent {
  @ViewChild(Chessboard) chessboard!: Chessboard;
  private agentService = inject(AgentService);

  onFenChange(newFen: string): void {
    console.log('FEN changed in AppComponent:', newFen);
    this.agentService.analysePosition(newFen);
  }

  onReset(): void {
    this.chessboard.reset();
  }
}