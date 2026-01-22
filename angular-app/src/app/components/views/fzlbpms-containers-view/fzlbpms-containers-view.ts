import { Component, OnInit, ChangeDetectionStrategy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface Container {
  id: string;
  name: string;
  image: string;
  state: string;
  status: string;
}

@Component({
  selector: 'app-fzlbpms-containers-view',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './fzlbpms-containers-view.html',
  styleUrls: ['./fzlbpms-containers-view.css'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FzlbpmsContainersView implements OnInit {
  containers = signal<Container[]>([]);

  async ngOnInit() {
    try {
      // Mocking container list
      const containers: Container[] = [
        { id: "1", name: "mock-container-1", image: "nginx:latest", state: "running", status: "Up 2 hours" },
        { id: "2", name: "mock-container-2", image: "postgres:13", state: "running", status: "Up 2 hours" }
      ];
      this.containers.set(containers);
    } catch (error) {
      console.error("Error fetching containers:", error);
    }
  }

  async getContainerLogs(id: string) {
    try {
      // Mocking logs
      const logs = [`Log line 1 for container ${id}`, `Log line 2 for container ${id}`];
      console.log(`Logs for container ${id}:`, logs);
    } catch (error) {
      console.error(`Error fetching logs for container ${id}:`, error);
    }
  }
}