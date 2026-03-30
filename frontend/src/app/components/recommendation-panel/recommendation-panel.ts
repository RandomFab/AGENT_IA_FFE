import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { AgentService } from '../../services/agent.service';

@Component({
  selector: 'app-recommendation-panel',
  standalone:true,
  imports: [CommonModule],
  templateUrl: './recommendation-panel.html',
  styleUrl: './recommendation-panel.scss',
})
export class RecommendationPanel {
  public agentService = inject(AgentService);
}
