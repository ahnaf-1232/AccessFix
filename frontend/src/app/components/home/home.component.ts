import { Component, OnInit } from "@angular/core";
import { AnalysisService } from "../../services/analysis.service";
import type { Analysis } from "src/app/models/analysis";
import { trigger, transition, style, animate } from "@angular/animations";
import type {
  ApexAxisChartSeries,
  ApexChart,
  ApexDataLabels,
  ApexPlotOptions,
  ApexYAxis,
  ApexLegend,
  ApexStroke,
  ApexXAxis,
  ApexFill,
  ApexTooltip,
} from "ng-apexcharts";

export type ChartOptions = {
  series: ApexAxisChartSeries | ApexAxisChartSeries[];
  chart: ApexChart;
  dataLabels: ApexDataLabels;
  plotOptions: ApexPlotOptions;
  yaxis: ApexYAxis;
  xaxis: ApexXAxis;
  fill: ApexFill;
  tooltip: ApexTooltip;
  stroke: ApexStroke;
  legend: ApexLegend;
};

@Component({
  selector: "app-home",
  templateUrl: "./home.component.html",
  styleUrls: ["./home.component.css"],
  animations: [
    trigger("fadeIn", [transition(":enter", [style({ opacity: 0 }), animate("300ms", style({ opacity: 1 }))])]),
    trigger("slideInRight", [
      transition(":enter", [
        style({ transform: "translateX(100%)", opacity: 0 }),
        animate("500ms ease-out", style({ transform: "translateX(0)", opacity: 1 })),
      ]),
    ]),
  ],
})
export class HomeComponent implements OnInit {
  report: Analysis | null = null;
  title = "AccessFix";
  code = "";
  url = "";
  fileContent: File | null = null;
  errorMessage = "";
  selectedFileName = "Select a file";
  loading = false;

  showChat = false;
  messages: { text: string; sender: string }[] = [];
  userInput = "";

  pieChartOptions: Partial<ChartOptions> | any;
  barChartOptions: Partial<ChartOptions> | any;

  constructor(private codeAnalysisService: AnalysisService) {}

  ngOnInit(): void {
    // Load initial data or perform setup tasks
  }

  calculateLevelChartData(): void {
    if (!this.report || !this.report.csv_file_path) {
      return;
    }

    const levels = this.report.csv_file_path.reduce((acc: { [key: string]: number }, item) => {
      acc[item.level] = (acc[item.level] || 0) + 1;
      return acc;
    }, {});

    this.pieChartOptions = {
      series: Object.values(levels),
      chart: {
        type: "pie",
        height: 350,
      },
      labels: Object.keys(levels),
      responsive: [{
        breakpoint: 480,
        options: {
          chart: {
            width: 200,
          },
          legend: {
            position: "bottom",
          },
        },
      }],
    };
  }

  initCharts(): void {
    this.calculateLevelChartData(); // Make sure data is ready

    // Bar Chart Initialization might depend on another type of data processing
    this.barChartOptions = {
      series: [{
        data: [10, 20, 30, 40] // Example data
      }],
      chart: {
        type: "bar",
        height: 350,
      },
      xaxis: {
        categories: ["Type 1", "Type 2", "Type 3", "Type 4"],
      },
      plotOptions: {
        bar: {
          horizontal: false,
        },
      },
      responsive: [{
        breakpoint: 480,
        options: {
          chart: {
            width: 200,
          },
          plotOptions: {
            bar: {
              horizontal: true,
            },
          },
        },
      }],
    };
  }

  handleSubmit(): void {
    this.errorMessage = "";
    this.loading = true;
    this.report = null;

    this.codeAnalysisService.analyzeCode(this.code).subscribe(
      response => {
        this.report = response;
        this.initCharts();
        this.loading = false;
      },
      error => {
        this.errorMessage = 'Error analyzing code. Please try again.';
        this.loading = false;
      }
    );
  }

  handleFileChange(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.fileContent = file;
      this.selectedFileName = file.name;
      this.code = ""; // Clear existing code if file is selected
    } else {
      this.errorMessage = "Please select a valid file.";
      this.selectedFileName = "Select a file";
    }
  }

  toggleChat(): void {
    this.showChat = !this.showChat;
  }

  sendMessage(): void {
    if (this.userInput.trim()) {
      const message = this.userInput.trim();
      this.messages.push({ text: message, sender: "user" });

      // Simulate a response for demonstration
      setTimeout(() => {
        this.messages.push({ text: "Echo: " + message, sender: "bot" });
        this.userInput = "";
      }, 500);
    }
  }

  downloadReport(): void {
    if (!this.report) {
      console.error("No report data available to download");
      return;
    }

    const blob = new Blob([JSON.stringify(this.report, null, 2)], { type: "text/plain" });
    const url = window.URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "report.txt";
    document.body.appendChild(anchor);
    anchor.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(anchor);
  }
}
