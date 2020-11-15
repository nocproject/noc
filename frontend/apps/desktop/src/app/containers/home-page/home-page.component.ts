import { Component, Inject, LOCALE_ID, OnInit } from '@angular/core';
import { WINDOW } from '@noc/auth';

@Component({
  selector: 'noc-home-page',
  template: `
    <p>Home page</p>
    <p>Locale is {{localeId}}</p>
    <p>base href is {{base}}</p>
    <p>The time is {{today | date:'long'}}</p>
    <p>Currency: {{c | currency }}</p>
    <p>Number: {{c | number}}</p>
    <p>Percent: {{p1 | number}} => {{p1 | percent}}</p>
    <p>Percent: {{p2 | number}} => {{p2 | percent}}</p>
    <input [(ngModel)]="minutes" />
    <p i18n="@@page.home.text.plural">Updated {minutes, plural, =0 {just now} =1 {one minute ago} other {{{minutes}} minutes ago}}</p>
    <p i18n="@@page.home.text">Create</p>
    <p>Status: {{status}}</p>
  `
})
export class HomePageComponent implements OnInit {
  base = this.window['_app_base'] || '/';
  today: number = Date.now();
  c = 1000_333.45;
  p1 = 0.28;
  p2 = 1.12;
  minutes = 3;
  status = $localize`:@@status.pending:PENDING`;

  constructor(
    @Inject(WINDOW) private window: any,
    @Inject(LOCALE_ID) public localeId: string
  ) {
  }

  ngOnInit(): void {
  }
}
