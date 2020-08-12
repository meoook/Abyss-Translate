import React from "react"
import ErrorMsg from "../ErrorMsg"

class FrameInput extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      highlight: false,
      errorMsg: null,
    }
    // this.onDrop = this.onFileDroped.bind(this)
    // Не биндим так как контекст this у стрелочных функций остается
  }
  componentDidMount() {
    this.fileSelector = this.buildFileSelector()
  }

  buildFileSelector() {
    const fileSelector = document.createElement("input")
    fileSelector.setAttribute("type", "file")
    fileSelector.addEventListener("change", this.onFileAdded)
    // fileSelector.setAttribute("multiple", "multiple")
    return fileSelector
  }

  checkFile(target) {
    if (target.files.length === 0) return
    this.setState({ highlight: true })
    const file = target.files[0]
    if (file.type.substring(0, 4) === "text" || file.type === "application/vnd.ms-excel") {
      this.props.onLoaded(file)
    } else {
      this.setState({ errorMsg: [`Income file not a text format`, file.name, file.type] })
    }
    this.setState({ highlight: false })
  }

  hideErrorMsg = () => {
    this.setState({ errorMsg: null })
  }

  openFileDialog = (event) => {
    this.fileSelector.click()
  }

  onFileAdded = (event) => {
    this.checkFile(event.target)
  }

  onFileDropped = (event) => {
    event.preventDefault()
    event.stopPropagation()
    this.checkFile(event.dataTransfer)
  }

  onDragOver = (event) => {
    event.preventDefault()
    event.stopPropagation()
    this.setState({ highlight: true })
  }

  onDragLeave = () => {
    this.setState({ highlight: false })
  }

  render() {
    return (
      <div
        className={this.state.highlight ? "file-input highlight" : "file-input"}
        onClick={this.openFileDialog}
        onDragOver={this.onDragOver}
        onDragLeave={this.onDragLeave}
        onDrop={this.onFileDropped}>
        {this.state.errorMsg && <ErrorMsg errorMsg={this.state.errorMsg} hideErrorMsg={this.hideErrorMsg} />}
        <h1>Click here to select file</h1>
        <div>Or drop file in this area</div>
      </div>
    )
  }
}

export default FrameInput
