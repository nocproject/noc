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
          i18n-placeholder="@@form.login.field.username.placeholder"
          placeholder="Username"
          formControlName="username"
        />
      </p>

      <p>
        <input
          type="password"
          i18n-placeholder="@@form.login.field.password.placeholder"
          placeholder="Password"
          formControlName="password"
        />
      </p>

      <p *ngIf="errorMessage">
        {{ errorMessage }}
      </p>

      <p>
        <button type="submit" i18n="@@form.login.button.login">Login</button>
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
