import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'noc-header',
  template: `
    <mat-toolbar color="primary" class="noc-toolbar">
      <button *ngIf="isAuth" mat-icon-button>
        <mat-icon>menu</mat-icon>
      </button>
      <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 500 500">
        <path fill="white"
              d="M120 500 L0 380 H45 V75 A75 75 0 0 1 180 30 L305 197 V120 H259 L380 0 L500 120 H455 V425 A75 75 0 0 1 319 469 L195 302 L195 380 H241 Z" />
      </svg>
      <span class="noc-app-name">NOC</span>
      <span class="noc-spacer"></span>
      <noc-lang-picker lang="{{lang}}" (langSwitchEvent)="langSwitch($event)"></noc-lang-picker>
      <button *ngIf="isAuth" mat-icon-button (click)="logout()">
        <mat-icon>exit_to_app</mat-icon>
      </button>
    </mat-toolbar>
  `,
  styleUrls: ['header-component.css']
})
export class HeaderComponent {
  @Input() isAuth: boolean;
  @Input() lang: string;
  @Output() readonly logoutEvent = new EventEmitter<void>();
  @Output() readonly langSwitchEvent = new EventEmitter<string>();

  langSwitch(code: string): void {
    this.langSwitchEvent.emit(code);
  }

  logout(): void {
    this.logoutEvent.emit();
  }
}
