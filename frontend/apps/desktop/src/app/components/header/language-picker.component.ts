import { Component, EventEmitter, Input, Output } from '@angular/core';

interface Language {
  code: string,
  label: string
}

@Component({
  selector: 'noc-lang-picker',
  template: `
    <button mat-button [matMenuTriggerFor]="languagePicker"
            i18n-aria-label="@@widget.language-picker.aria-label"
            aria-label="Select a language"
            i18n-matTooltip="@@widget.language-picker.tooltip"
            matTooltip="Select a language of the NOC-ui">
      <mat-icon>language</mat-icon>
      {{lang}}
      <mat-icon>arrow_drop_down</mat-icon>
    </button>
    <mat-menu #languagePicker="matMenu">
      <button mat-menu-item *ngFor="let lang of availableLocale()" (click)="langSwitch(lang.code)">
        {{lang.label}}
      </button>
    </mat-menu>
  `
})
export class LanguagePicker {
  @Input() lang: string;
  @Output() readonly langSwitchEvent = new EventEmitter<string>();
  languages: Array<Language> = [
    { code: 'en', label: 'English' },
    { code: 'ru', label: 'Русский' }
  ];

  availableLocale(): Array<Language> {
    return this.languages.filter(l => l.code !== this.lang);
  }

  langSwitch(localeId: string): void {
    this.langSwitchEvent.emit(localeId);
  }
}
