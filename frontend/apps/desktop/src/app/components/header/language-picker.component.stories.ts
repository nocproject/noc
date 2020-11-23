import { select } from '@storybook/addon-knobs';

import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatMenuModule } from '@angular/material/menu';

import { LanguagePicker } from './language-picker.component';

export default {
  title: 'Language Picker'
};

export const primary = () => ({
  moduleMetadata: {
    imports: [
      BrowserAnimationsModule,
      MatButtonModule,
      MatIconModule,
      MatMenuModule,
      MatTooltipModule
    ]
  },
  component: LanguagePicker,
  props: {
    lang: select<string>('Language', ['en', 'ru'], 'ru')
  }
});
