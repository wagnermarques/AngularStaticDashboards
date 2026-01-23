import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { catchError, map, of, switchMap } from 'rxjs';

@Component({
  selector: 'app-duplicates-view',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './duplicates-view.html',
  styleUrl: './duplicates-view.css',
})
export class DuplicatesView {
  private http = inject(HttpClient);
  private sanitizer = inject(DomSanitizer);

  years = ['2021', '2022', '2023'];
  selectedYear = signal<string>('2023');

  duplicatesHtml = toSignal(
    toObservable(this.selectedYear).pipe(
      switchMap(year => 
        this.http.get(`assets/data_analysis/duplicates_${year}.html`, { responseType: 'text' }).pipe(
          map(html => this.sanitizer.bypassSecurityTrustHtml(html)),
          catchError(() => of(this.sanitizer.bypassSecurityTrustHtml('<p class="text-info">Nenhum registro duplicado detectado para este ano.</p>')))
        )
      )
    )
  );

  setYear(year: string) {
    this.selectedYear.set(year);
  }
}