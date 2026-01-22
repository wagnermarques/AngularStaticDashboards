import { Component, inject, OnInit, signal, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import * as d3 from 'd3';

interface PipelineStep {
  id: string;
  label: string;
  status: 'pending' | 'completed' | 'error';
}

@Component({
  selector: 'app-view-home',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './view-home.html',
  styleUrl: './view-home.css',
})
/**
 * ViewHome
 *
 * Componente responsável por carregar e exibir:
 * - um gráfico externo (iframe) com contagem de estudantes por ano (chartUrl),
 * - um grafo de pipeline renderizado com D3 baseado em dados locais (pipelineSteps).
 *
 * Principais responsabilidades:
 * - recuperar dados JSON com HttpClient e popular pipelineSteps (sinal reativo),
 * - renderizar um grafo SVG via D3 dentro de um container referenciado no template,
 * - construir e sanitizar a URL do iframe do gráfico com cache-busting.
 *
 * Propriedades:
 * - pipelineSteps: signal<PipelineStep[]>
 *   Sinal reativo que mantém a lista de passos do pipeline carregada de assets/data_analysis/pipeline_graph.json.
 *
 * - chartUrl: signal<SafeResourceUrl | null>
 *   Sinal reativo que contém a URL sanitizada do recurso HTML do gráfico (assets/data_analysis/student_count_by_year.html?t=...).
 *
 * - @ViewChild('d3Container') d3Container!: ElementRef;
 *   Explicação detalhada (em Português):
 *   - O decorator @ViewChild('d3Container') instrui o Angular a procurar, no template deste componente,
 *     um elemento que tenha a referência de template com nome "d3Container" (ex.: <div #d3Container></div>).
 *   - Quando encontrado, o Angular injeta uma referência desse elemento na propriedade `d3Container`.
 *   - O tipo ElementRef representa uma referência wrapper para o elemento DOM nativo; o DOM real fica acessível
 *     através de `d3Container.nativeElement`.
 *   - O operador de afirmação não-nula `!` (postfix) indica ao compilador TypeScript que esta propriedade será
 *     inicializada pelo Angular e, portanto, não será `undefined` quando for utilizada em tempo de execução.
 *     Isso evita erros de compilação relacionados a "possibly undefined".
 *   - Por padrão (@ViewChild static = false), essa referência só estará disponível após a inicialização da view,
 *     ou seja, dentro/apos ngAfterViewInit. Tentar acessar `d3Container.nativeElement` em ngOnInit pode resultar
 *     em referência não inicializada.
 *   - Observações práticas: para manipular o DOM com D3 o acesso via nativeElement é comum; porém em cenários
 *     de Server-Side Rendering (SSR) ou para maior testabilidade/portabilidade, considere usar Renderer2
 *     ou condicionar a execução apenas no ambiente cliente.
 *   - Dica: declarar como ElementRef<HTMLElement> melhora a tipagem (ElementRef<HTMLDivElement> se for um div).
 *
 * Métodos principais:
 * - ngOnInit(): carrega a URL do gráfico (loadChart).
 * - ngAfterViewInit(): inicia o carregamento dos dados do pipeline e a renderização do grafo (loadPipelineGraph).
 * - loadPipelineGraph(): realiza GET do JSON, atualiza pipelineSteps e chama renderD3Graph com pequeno timeout.
 * - renderD3Graph(steps: PipelineStep[]): renderiza SVG contendo linhas (ligações) e nós (círculos + textos) usando D3.
 * - loadChart(): constrói a URL do recurso do gráfico com timestamp para evitar cache e aplica DomSanitizer.bypassSecurityTrustResourceUrl.
 *
 * Exemplo de uso (template):
 * <div #d3Container class="pipeline-graph"></div>
 * <iframe [src]="chartUrl()"></iframe>
 *
 * Observações de segurança e boas práticas:
 * - DOM direto via ElementRef.nativeElement é poderoso mas requer cuidado (XSS, SSR).
 * - Sanitizar URLs externas/embedded é essencial (uso de DomSanitizer já presente).
 * - Preferir tipar ElementRef com o tipo específico do elemento para melhor autocompletar/checagem.
 */
export class ViewHome implements OnInit, AfterViewInit {
  private http = inject(HttpClient);
  private sanitizer = inject(DomSanitizer);
  
  @ViewChild('d3Container') d3Container!: ElementRef;

  pipelineSteps = signal<PipelineStep[]>([]);
  chartUrl = signal<SafeResourceUrl | null>(null);

  ngOnInit() {
    this.loadChart();
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
    const height = steps.length * 100; // Vertical height based on steps

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

  loadChart() {
    const timestamp = new Date().getTime();
    this.chartUrl.set(
      this.sanitizer.bypassSecurityTrustResourceUrl(`assets/data_analysis/student_count_by_year.html?t=${timestamp}`)
    );
  }
}