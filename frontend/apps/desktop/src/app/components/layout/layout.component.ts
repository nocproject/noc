import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'noc-layout',
  template: `
    <div class="layout-container">
      <noc-header [lang]="lang"
                  [isAuth]="isAuth"
                  (langSwitchEvent)="langSwitch($event)"
                  (logoutEvent)="logout()"></noc-header>
      <mat-sidenav-container class="sidenav-container" hasBackdrop="false">
        <mat-sidenav opened="true" mode="side">Start</mat-sidenav>
        <mat-sidenav opened="true" mode="side" position="end">End</mat-sidenav>
        <main>
          <ng-content></ng-content>
        </main>
      </mat-sidenav-container>
    </div>
  `,
  styles: [
      `
          .layout-container {
              height: 100%;
              display: flex;
              flex-direction: column;
          }`,
      `
          .sidenav-container {
              height: 100%;
          }`
  ]
})
export class LayoutComponent {
  @Input() isAuth: boolean;
  @Input() lang: string;
  @Output() readonly logoutEvent = new EventEmitter<void>();
  @Output() readonly langSwitchEvent = new EventEmitter<string>();

  logout() {
    this.logoutEvent.emit();
  }

  langSwitch(code: string) {
    this.langSwitchEvent.emit(code);
  }
}
