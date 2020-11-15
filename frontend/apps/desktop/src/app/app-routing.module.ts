import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { HomePageComponent } from './containers';

const routes: Routes = [
  {
    path: 'home',
    component: HomePageComponent
  },
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
  {
    path: '',
    redirectTo: '/home',
    pathMatch: 'full'
  }
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes, { initialNavigation: 'enabled' })
  ],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
