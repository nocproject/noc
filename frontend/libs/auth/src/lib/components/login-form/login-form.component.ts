import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';

import { Credentials } from '../../models';

@Component({
  selector: 'auth-login-form',
  template: `
    <mat-card class="login-form">
      <mat-card-content>
        <form [formGroup]="form" (ngSubmit)="submit()">
          <h2 i18n="@@form.login.title">Log In</h2>
          <mat-error *ngIf="errorMessage">
            {{ errorMessage }}
          </mat-error>
          <mat-form-field class="login-form-field" appearance="standard">
            <mat-label i18n="@@form.login.field.username.label">Username</mat-label>
            <input
              type="text"
              matInput
              formControlName="username"
            />
          </mat-form-field>
          <br />
          <mat-form-field class="login-form-field" appearance="standard">
            <mat-label i18n="@@form.login.field.password.label">Password</mat-label>
            <input
              type="password"
              matInput
              formControlName="password"
            />
          </mat-form-field>
          <br />
          <button type="submit" i18n="@@form.login.button.login" mat-button color="primary">Login</button>
        </form>
      </mat-card-content>
    </mat-card>
  `,
  styles: [
      `
          .login-form {
              text-align: center;
              margin: 2em auto;
              max-width: 600px;
          }`,
      `
          .login-form-field {
              width: 400px;
          }`
  ]
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
