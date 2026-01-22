import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { MatCardModule } from '@angular/material/card';

interface YearStat {
  year: string;
  student_count: number;
}

@Component({
  selector: 'app-census-analysis',
  standalone: true,
  imports: [CommonModule, MatCardModule],
  templateUrl: './census-analysis.html',
  styleUrl: './census-analysis.css'
})
export class CensusAnalysisComponent implements OnInit {
  data: YearStat[] = [];
  plotlyChartUrl: SafeResourceUrl | null = null;

  constructor(private http: HttpClient, private sanitizer: DomSanitizer) {}

  ngOnInit(): void {
    this.http.get<YearStat[]>('assets/data_analysis/summary_stats.json')
      .subscribe({
        next: (data) => {
          this.data = data;
        },
        error: (err) => console.error('Failed to load summary stats', err)
      });

    const unsafeUrl = 'assets/data_analysis/student_count_by_year.html';
    this.plotlyChartUrl = this.sanitizer.bypassSecurityTrustResourceUrl(unsafeUrl);
  }
}