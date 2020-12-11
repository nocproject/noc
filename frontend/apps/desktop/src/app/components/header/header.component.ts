import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'noc-header',
  templateUrl: 'header-component.html',
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
