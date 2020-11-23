import { boolean, select } from '@storybook/addon-knobs';

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatToolbarModule } from '@angular/material/toolbar';

import { HeaderComponent } from './header.component';
import { LanguagePicker } from './language-picker.component';

export default {
  title: 'Header'
};

export const primary = () => ({
  moduleMetadata: {
    imports: [
      BrowserAnimationsModule,
      MatButtonModule,
      MatIconModule,
      MatMenuModule,
      MatToolbarModule
    ],
    declarations: [
      LanguagePicker
    ]
  },
  component: HeaderComponent,
  props: {
    isAuth: boolean('isAuth', false),
    lang: select<string>('Language', ['en', 'ru'], 'ru')
  }
});
