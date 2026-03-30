import { Component } from '@angular/core';
import { Chessboard } from './components/chessboard/chessboard';
import { RecommendationPanel } from "./components/recommendation-panel/recommendation-panel";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [Chessboard, RecommendationPanel],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class AppComponent {}