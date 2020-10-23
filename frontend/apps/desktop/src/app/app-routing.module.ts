import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

// import { WelcomeComponent } from './welcome.component';

const routes: Routes = [
  // {
  //   path: 'welcome',
  //   component: WelcomeComponent
  // },
  // {
  //   path: 'admin',
  //   loadChildren: () =>
  //     import('@noc-nx/admin').then(module => module.AdminModule),
  // },
  // {
  //   path: 'monitoring',
  //   loadChildren: () =>
  //     import('@noc-nx/monitor').then(module => module.MonitorModule),
  // },
  // {
  //   path: '',
  //   redirectTo: '/welcome',
  //   pathMatch: 'full'
  // }
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes, { initialNavigation: 'enabled' })
  ],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
