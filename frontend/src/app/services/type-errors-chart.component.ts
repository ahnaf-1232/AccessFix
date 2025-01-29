import { Component, Input, ViewChild, ElementRef, OnChanges, SimpleChanges, AfterViewInit } from "@angular/core";
import { Chart, type ChartConfiguration } from "chart.js/auto";

@Component({
  selector: "app-type-errors-chart",
  template: "<canvas #chartCanvas></canvas>", 
})
export class TypeErrorsChartComponent implements OnChanges, AfterViewInit {
  @Input() data: { type: string; count: number }[] = [];
  @ViewChild('chartCanvas') chartCanvas!: ElementRef<HTMLCanvasElement>;
  chart: Chart | undefined;

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['data'] && this.data) {
      if (this.chart) {
        this.updateChartData();
      }
    }
  }

  ngAfterViewInit(): void {
    this.createChart();
  }

  updateChartData(): void {
    if (this.chart && this.data) {
      this.chart.data.labels = this.data.map(item => this.mapTypeToLabel(item.type));
      this.chart.data.datasets.forEach(dataset => {
        dataset.data = this.data.map(item => item.count);
      });
      this.chart.update();
    }
  }

  createChart(): void {
    if (this.chartCanvas && this.chartCanvas.nativeElement) {
      if (this.chart) {
        this.chart.destroy();
      }

      const config: ChartConfiguration = {
        type: 'pie',
        data: {
          labels: this.data.map(item => this.mapTypeToLabel(item.type)),
          datasets: [
            {
              data: this.data.map(item => item.count),
              backgroundColor: [
                "rgba(255, 99, 132, 0.8)",
                "rgba(54, 162, 235, 0.8)",
                "rgba(255, 206, 86, 0.8)",
                "rgba(75, 192, 192, 0.8)"
              ]
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              position: 'bottom',
            },
            title: {
              display: true,
              text: 'Errors by Type',
            }
          }
        }
      };

      this.chart = new Chart(this.chartCanvas.nativeElement, config);
    }
  }

  private mapTypeToLabel(type: string): string {
    const typeMap: { [key: string]: string } = {
      '1': 'Perceivable',
      '2': 'Operable',
      '3': 'Understandable',
      '4': 'Robust'
    };
    return typeMap[type] || 'Unknown Type'; // Fallback for unmatched types
  }
}
