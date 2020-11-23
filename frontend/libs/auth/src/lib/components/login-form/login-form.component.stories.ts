import { text } from '@storybook/addon-knobs';

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ReactiveFormsModule } from '@angular/forms';

import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

import { LayoutModule } from '@angular/cdk/layout';

import { LoginFormComponent } from './login-form.component';

export default {
  title: 'Login Form'
};

export const primary = () => ({
  moduleMetadata: {
    imports: [
      BrowserAnimationsModule,
      ReactiveFormsModule,
      MatButtonModule,
      MatCardModule,
      MatFormFieldModule,
      MatInputModule,
      LayoutModule
    ]
  },
  component: LoginFormComponent,
  props: {
    errorMessage: text('errorMessage', 'zzzz')
  }
});
