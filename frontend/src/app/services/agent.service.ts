import { inject, Injectable } from "@angular/core";
import { BehaviorSubject, map, Subject, switchMap, tap, of, catchError } from "rxjs";
import { AgentInput, RequestState } from "../models/agent.model";
import { AgentOutput } from "../models/agent.model";
import { ApiService } from "./api.service";

@Injectable({ providedIn: 'root' })

export class AgentService {
    private api = inject(ApiService);

    private readonly INITIAL_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

    private analyzeRequest$ = new Subject<string>();

    private state = new BehaviorSubject<RequestState<AgentOutput>>({
        data: null,
        isLoading: false,
        error: null
    });

    public state$ = this.state.asObservable();

    constructor() {
        this.setupAnalysisPipeline();
    }


    analysePosition(fen: string): void {
        console.log('Analyzing position with FEN:', fen);
    if (fen === this.INITIAL_FEN) {
      console.log('Position initiale détectée, skip analyse');
      // Réinitialiser l'état
      this.state.next({
        data: null,
        isLoading: false,
        error: null
      });
      return;
    }        
        this.analyzeRequest$.next(fen);
    }

    private setupAnalysisPipeline(): void {
        this.analyzeRequest$.pipe(
            //set at loading state
            tap(() => {
                console.log('State : Loading');
                this.state.next({
                    data: null,
                    isLoading: true,
                    error: null
                });
            }),

            switchMap(fen => this.api.post<AgentOutput, AgentInput>('agent', { fen, depth: 5, max_articles: 5, max_video: 3 }).pipe(
                map(response=> {
                    console.log('Received response from API:', response);
                    return {data:response, isLoading: false, error: null};
                }),
                catchError(error => {
                    console.error('Error during API call:', error);
                    return of({
                        data: null,
                        isLoading: false,
                        error: 'Failed to analyze position. Please try again.'
                    });
                })  
            )
            )
        ).subscribe(result => {
                this.state.next(result);
            });
    }
}