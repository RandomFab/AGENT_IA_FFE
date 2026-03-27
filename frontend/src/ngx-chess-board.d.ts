declare module 'ngx-chess-board' {
  import { ModuleWithProviders, NgModule } from '@angular/core';

  export class NgxChessBoardModule {
    static forRoot(): ModuleWithProviders<NgxChessBoardModule>;
  }

  export class NgxChessBoardComponent {
    reset(): void;
    reverse(): void;
    undo(): void;
    getMoveHistory(): any[];
    setFEN(fen: string): void;
    getFEN(): string;
    move(coords: string): void;
  }

  export class NgxChessBoardView extends NgxChessBoardComponent {}
}