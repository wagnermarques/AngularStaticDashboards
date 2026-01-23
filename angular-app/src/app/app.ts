import { Component, ViewChild, HostListener, OnInit, inject } from '@angular/core';
import { RouterOutlet, RouterLink } from '@angular/router';
import { FixedHead } from './components/layout/fixed-head/fixed-head';
import { FixedStatusbar } from "./components/layout/fixed-statusbar/fixed-statusbar";

import { MatSidenavModule, MatDrawer } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { SwUpdate, VersionReadyEvent } from '@angular/service-worker';
import { filter } from 'rxjs';

@Component({
  selector: 'app-root',
  templateUrl: './app.html',
  styleUrl: './app.css',
  imports: [
    RouterOutlet, 
    RouterLink,
    MatSidenavModule,
    MatListModule,
    MatIconModule,
    MatDividerModule,
    FixedHead, 
    FixedStatusbar
  ],
})
export class App implements OnInit {
  @ViewChild('drawer') drawer!: MatDrawer;
  isSmallScreen = false;

  private swUpdate = inject(SwUpdate);

  constructor() {
    this.checkScreenSize();
    this.checkForUpdates();
  }

  ngOnInit() {
    this.setupLogListener();
  }

  checkForUpdates() {
    if (this.swUpdate.isEnabled) {
      this.swUpdate.versionUpdates
        .pipe(filter((evt): evt is VersionReadyEvent => evt.type === 'VERSION_READY'))
        .subscribe(evt => {
          console.log('Nova versÃ£o detectada:', evt.latestVersion.hash);
          if (confirm('Uma nova versÃ£o do dashboard estÃ¡ disponível. Atualizar agora?')) {
            window.location.reload();
          }
        });
    }
  }

  /**
   * Mock log listener since Tauri is removed.
   */
  async setupLogListener() {
    console.log("Log listener setup (mocked).");
  }

  @HostListener('window:resize')
  onResize() {
    this.checkScreenSize();
  }
  
  toggleDrawer() {
    this.drawer.toggle();
  }

  checkScreenSize() {
    this.isSmallScreen = window.innerWidth < 768;
  }
}
