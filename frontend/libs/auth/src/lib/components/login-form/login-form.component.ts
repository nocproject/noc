import { Component, Input, OnInit, Output, EventEmitter } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';

import { Credentials } from '../../models';

@Component({
  selector: 'auth-login-form',
  template: `
    <form [formGroup]="form" (ngSubmit)="submit()">
      <p>
        <input
          type="text"
          placeholder="Username"
          formControlName="username"
        />
      </p>

      <p>
        <input
          type="password"
          placeholder="Password"
          formControlName="password"
        />
      </p>

      <p *ngIf="errorMessage">
        {{ errorMessage }}
      </p>

      <p class="loginButtons">
        <button type="submit">Login</button>
      </p>
    </form>
  `
})
export class LoginFormComponent implements OnInit {
  @Input() errorMessage!: string | null;
  @Input()
  set pending(isPending: boolean | null) {
    if (isPending) {
      this.form.disable();
    } else {
      this.form.enable();
    }
  }
  @Output() submitted = new EventEmitter<Credentials>();

  form: FormGroup = new FormGroup({
    username: new FormControl('admin'),
    password: new FormControl('')
  });

  constructor() {
  }

  ngOnInit(): void {
  }

  submit() {
    if (this.form.valid) {
      this.submitted.emit(this.form.value);
    }
  }
}
