import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { catchError, map, of, switchMap } from 'rxjs';

@Component({
  selector: 'app-dictionary-view',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dictionary-view.html',
  styleUrl: './dictionary-view.css',
})
export class DictionaryView {
  private http = inject(HttpClient);
  private sanitizer = inject(DomSanitizer);

  years = ['2021', '2022', '2023'];
  selectedYear = signal<string>('2023');

  dictionaryHtml = toSignal(
    toObservable(this.selectedYear).pipe(
      switchMap(year => 
        this.http.get(`assets/data_analysis/dictionary_${year}.html`, { responseType: 'text' }).pipe(
          map(html => this.sanitizer.bypassSecurityTrustHtml(html)),
          catchError(() => of(this.sanitizer.bypassSecurityTrustHtml('<p class="text-danger">Erro ao carregar dicionário.</p>')))
        )
      )
    )
  );

  setYear(year: string) {
    this.selectedYear.set(year);
  }
}