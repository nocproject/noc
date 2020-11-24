import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Component({
  selector: 'noc-test-page',
  template: `
    <p>Test page</p>
    <p>Id is {{ id$ | async}}</p>
  `
})
export class TestPageComponent {
  id$: Observable<number> = this.route.params.pipe(map(p => p.id));

  constructor(public route: ActivatedRoute) {
  }
}
