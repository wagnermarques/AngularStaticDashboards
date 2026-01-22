import { Component, inject, OnInit, signal, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import * as d3 from 'd3';

interface PipelineStep {
  id: string;
  label: string;
  status: 'pending' | 'completed' | 'error';
}

@Component({
  selector: 'app-pipeline-view',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './pipeline-view.html',
  styleUrl: './pipeline-view.css',
})
export class PipelineView implements OnInit, AfterViewInit {
  private http = inject(HttpClient);

  @ViewChild('d3Container') d3Container!: ElementRef;

  pipelineSteps = signal<PipelineStep[]>([]);

  ngOnInit() {
  }

  ngAfterViewInit() {
    this.loadPipelineGraph();
  }

  loadPipelineGraph() {
    this.http.get<PipelineStep[]>('assets/data_analysis/pipeline_graph.json')
      .subscribe({
        next: (data) => {
          this.pipelineSteps.set(data);
          setTimeout(() => this.renderD3Graph(data), 100);
        },
        error: (err) => console.error('Error loading pipeline graph:', err)
      });
  }

  renderD3Graph(steps: PipelineStep[]) {
    if (!this.d3Container) return;

    const container = this.d3Container.nativeElement;
    const width = container.offsetWidth || 400;
    const height = steps.length * 100;

    d3.select(container).selectAll('*').remove();

    const svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    const nodes = steps.map((s, i) => ({ 
      ...s, 
      x: width / 2, 
      y: (i + 1) * 80 
    }));
    
    const links = [];
    for (let i = 0; i < nodes.length - 1; i++) {
      links.push({ source: nodes[i], target: nodes[i + 1] });
    }

    svg.selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y)
      .attr('stroke', '#999')
      .attr('stroke-width', 2);

    const nodeGroups = svg.selectAll('g')
      .data(nodes)
      .enter()
      .append('g')
      .attr('transform', d => `translate(${d.x},${d.y})`);

    nodeGroups.append('circle')
      .attr('r', 25)
      .attr('fill', d => {
        if (d.status === 'completed') return '#4caf50';
        if (d.status === 'error') return '#f44336';
        return '#2196f3';
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    nodeGroups.append('text')
      .attr('dy', 5)
      .attr('text-anchor', 'middle')
      .attr('fill', '#fff')
      .attr('font-size', '16px')
      .attr('pointer-events', 'none')
      .text(d => {
        if (d.status === 'completed') return '✓';
        if (d.status === 'error') return '✗';
        return '⋯';
      });

    nodeGroups.append('text')
      .attr('dx', 40)
      .attr('dy', 5)
      .attr('text-anchor', 'start')
      .attr('fill', '#333')
      .attr('font-size', '14px')
      .attr('font-weight', 'bold')
      .text(d => d.label);
  }
}
