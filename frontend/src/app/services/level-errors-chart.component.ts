import { Component, Input, ViewChild, ElementRef, OnChanges, SimpleChanges, AfterViewInit } from "@angular/core";
import { Chart, type ChartConfiguration } from "chart.js/auto";

@Component({
  selector: "app-level-errors-chart",
  template: "<canvas #chartCanvas></canvas>",
  // styleUrls: ['./level-errors-chart.component.css'] // Add if you have specific styles
})
export class LevelErrorsChartComponent implements OnChanges, AfterViewInit {
  @Input() data: { level: string; count: number }[] = [];
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
      this.chart.data.labels = this.data.map(item => item.level);
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
        type: 'bar',
        data: {
          labels: this.data.map(item => item.level),
          datasets: [
            {
              label: 'Errors by Level',
              data: this.data.map(item => item.count),
              backgroundColor: ['rgba(255, 99, 132, 0.8)' , 'rgba(255, 206, 86, 0.8)' , 'rgba(54, 162, 235, 0.8)']
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          }
        }
      };

      this.chart = new Chart(this.chartCanvas.nativeElement, config);
    }
  }
}
