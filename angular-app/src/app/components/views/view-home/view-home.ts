import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

@Component({
  selector: 'app-view-home',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './view-home.html',
  styleUrl: './view-home.css',
})
export class ViewHome implements OnInit {
  private http = inject(HttpClient);
  private sanitizer = inject(DomSanitizer);

  chartUrl = signal<SafeResourceUrl | null>(null);

  ngOnInit() {
    this.loadChart();
  }

  loadChart() {
    const timestamp = new Date().getTime();
    this.chartUrl.set(
      this.sanitizer.bypassSecurityTrustResourceUrl(`assets/data_analysis/student_count_by_year.html?t=${timestamp}`)
    );
  }
}