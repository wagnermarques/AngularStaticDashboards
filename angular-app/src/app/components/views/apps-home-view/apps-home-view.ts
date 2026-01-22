import { Component, OnInit, ChangeDetectionStrategy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { Router } from '@angular/router';

export interface Project {
  name: string;
  url: string;
}

@Component({
  selector: 'app-apps-home-view',
  standalone: true,
  imports: [CommonModule, MatButtonModule],
  templateUrl: './apps-home-view.html',
  styleUrls: ['./apps-home-view.css'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AppsHomeView implements OnInit {
  projects = signal<Project[]>([]);
  installationProgress = signal<string[]>([]);

  constructor(private router: Router) {}

  async ngOnInit() {
    try {
      // Mocking projects
      const projects: Project[] = [
        { name: "Project A", url: "http://localhost:4200/project-a" },
        { name: "Project B", url: "http://localhost:4200/project-b" }
      ];
      this.projects.set(projects);
    } catch (error) {
      console.error("Error fetching projects:", error);
    }
    
    // Mocking listener
    console.log("Mocking moodle-installation-progress listener.");
  }

  async openUrl(url: string) {
    try {
      console.log(`Mock opening url: ${url}`);
      window.open(url, '_blank');
    } catch (error) {
      console.error(`Error opening url ${url}:`, error);
    }
  }

  async installMoodle() {
    this.router.navigate(['/moodle-install']);
  }

  installJoomla() {
    console.log("Install Joomla button clicked");
  }

  createAngularApp() {
    console.log("Create Angular App button clicked");
  }
}