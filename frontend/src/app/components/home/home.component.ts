import { Component, OnInit } from "@angular/core"
import { AnalysisService } from "../../services/analysis.service"
import type { Analysis } from "src/app/models/analysis"
import { HttpClient } from "@angular/common/http"
import { trigger, transition, style, animate } from "@angular/animations"
import jsPDF from "jspdf"



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
export class HomeComponent {
  report: Analysis | null = null
  title = "AccessFix"
  code = ""
  url = ""
  fileContent: File | null = null
  errorMessage = ""
  selectedFileName = "Select a file"
  loading = false

  showChat = false
  messages: { text: string; sender: string }[] = []
  userInput = ""
  cardStates: boolean[] = []

  levelErrors: { level: string; count: number }[] = []
  typeErrors: { type: string; count: number }[] = []


  constructor(
    private codeAnalysisService: AnalysisService,
    private http: HttpClient,
  ) {
  }


  processAnalysisData() {
    if (this.report && this.report.csv_file_path) {
      // Process level errors
      const levelCounts: { [key in 'A' | 'AA' | 'AAA']: number } = { A: 0, AA: 0, AAA: 0 }
      this.report.csv_file_path.forEach((detail) => {
        if (levelCounts.hasOwnProperty(detail.level)) {
          levelCounts[detail.level as 'A' | 'AA' | 'AAA']++
        }
      })
      this.levelErrors = Object.entries(levelCounts).map(([level, count]) => ({ level, count }))

      // Process type errors
      const typeCounts: { [key: string]: number } = {}
      this.report.csv_file_path.forEach((detail) => {
        const type = detail.reference.split(".")[0]
        typeCounts[type] = (typeCounts[type] || 0) + 1
      })
      this.typeErrors = Object.entries(typeCounts).map(([type, count]) => ({ type, count: count as number }))
    }
  }




  toggleCard(index: number) {
    this.cardStates[index] = !this.cardStates[index]
  }  

  copyCodeToClipboard() {
    if (this.report && this.report.corrected_html) {
      navigator.clipboard.writeText(this.report.corrected_html).then(
        () => {
          // You can add a notification here to inform the user that the code was copied
          console.log("Code copied to clipboard")
        },
        (err) => {
          console.error("Could not copy text: ", err)
        },
      )
    }
  }

  handleSubmit(): void {
    this.errorMessage = ""
    this.loading = true
    this.report = null

    if (this.code) {
      this.codeAnalysisService.analyzeCode(this.code).subscribe(
        (response) => {
          this.report = response
          this.loading = false
          this.processAnalysisData() 
        },
        (error) => {
          console.error("Error during code analysis:", error)
          this.loading = false
        },
      )
    } else if (this.url) {
      this.codeAnalysisService.analyzeUrl(this.url).subscribe(
        (response) => {
          this.report = response
          // this.clearFields();
          this.loading = false
          this.processAnalysisData() 
        },
        (error) => {
          this.errorMessage = "Error analyzing URL."
          this.loading = false
        },
      )
    } else if (this.fileContent) {
      const file = this.fileContent // Directly use the file here, not FormData

      // Send file object to analyzeFile method
      this.codeAnalysisService.analyzeFile(file).subscribe(
        (response) => {
          this.report = response
          // this.clearFields();
          this.loading = false
          this.processAnalysisData() 
        },
        (error) => {
          this.errorMessage = "Error analyzing file."
          this.loading = false
        },
      )
    } else {
      this.errorMessage = "Please enter code, select a file, or enter a URL."
      this.loading = false
    }
  }

  handleFileChange(input: any): void {
    const file = input.files[0]
    if (file) {
      this.fileContent = file
      this.code = "" // Clear code if file is selected
      this.selectedFileName = file.name
    } else {
      this.errorMessage = "Please select a valid file."
      this.selectedFileName = "Select a file"
    }
  }

  toggleChat() {
    this.showChat = !this.showChat
    if (!this.showChat) {
      this.messages = [] // Clean chat when closed
    }
  }

  sendMessage() {
    if (this.userInput.trim()) {
      const userInput = this.userInput.trim()
      this.messages.push({ text: userInput, sender: "user" })

      this.codeAnalysisService.chatResponse(userInput).subscribe(
        (response) => {
          this.messages.push({ text: response.text, sender: "bot" })
          this.userInput = ""
        },
        (error) => {
          console.error(`Error fetching response: ${error}`) // Debug error
          this.errorMessage = "Error fetching response."
        },
      )
    }
  }

  downloadReport() {
    if (!this.report || !this.report.csv_file_path) {
      console.error("No report data available")
      return
    }

    const pdf = new jsPDF()
    let yOffset = 10

    // Add title
    pdf.setFontSize(20)
    pdf.text("Accessibility Analysis Report", 10, yOffset)
    yOffset += 10

    // Add summary
    pdf.setFontSize(12)
    pdf.text(`Total Initial Severity Score: ${this.report.total_initial_severity_score}`, 10, yOffset)
    yOffset += 7
    pdf.text(`Total Final Severity Score: ${this.report.total_final_severity_score}`, 10, yOffset)
    yOffset += 7
    pdf.text(`Total Improvement: ${this.report.total_improvement.toFixed(2)}%`, 10, yOffset)
    yOffset += 10

    // Add guideline details
    pdf.setFontSize(16)
    pdf.text("Guideline Details:", 10, yOffset)
    yOffset += 10

    pdf.setFontSize(10)
    this.report.csv_file_path.forEach((detail, index) => {
      if (yOffset > 280) {
        pdf.addPage()
        yOffset = 10
      }
      pdf.text(`${index + 1}. Error: ${detail.error}`, 10, yOffset)
      yOffset += 5
      pdf.text(`   Level: ${detail.level}`, 10, yOffset)
      yOffset += 5
      pdf.text(`   Reference: ${detail.reference}`, 10, yOffset)
      yOffset += 5
      pdf.text(`   Fix: ${detail.fix}`, 10, yOffset)
      yOffset += 5
      pdf.text(`   Description: ${detail.description}`, 10, yOffset)
      yOffset += 10
    })

    // Add corrected HTML
    if (yOffset > 280) {
      pdf.addPage()
      yOffset = 10
    }
    pdf.setFontSize(16)
    pdf.text("Corrected HTML:", 10, yOffset)
    yOffset += 10

    pdf.setFontSize(8)
    const splitHtml = pdf.splitTextToSize(this.report.corrected_html, 180)
    pdf.text(splitHtml, 10, yOffset)

    // Save the PDF
    pdf.save("accessibility_report.pdf")
  }

  clearFields(): void {
    this.code = ""
    this.url = ""
    this.fileContent = null
    this.selectedFileName = "Select a file"
  }
}

