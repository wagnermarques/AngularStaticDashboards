import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CensusAnalysisComponent } from './census-analysis';

describe('CensusAnalysisComponent', () => {
  let component: CensusAnalysisComponent;
  let fixture: ComponentFixture<CensusAnalysisComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CensusAnalysisComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CensusAnalysisComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeDefined();
  });
});
