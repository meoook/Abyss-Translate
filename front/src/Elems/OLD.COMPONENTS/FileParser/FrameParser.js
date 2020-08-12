import React from "react"
import TopBar from "./TopBar"
import FilePreview from "./FilePreview"

class FrameParser extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      filename: props.file.name,
      lines: [],
    }
  }

  componentDidMount() {
    const reader = new FileReader()
    reader.readAsText(this.props.file)
    reader.onload = () => {
      let lines = reader.result.split("\n") //.map((line) => line.split(","))
      this.setState({ lines })
    }
  }

  render() {
    return (
      <React.Fragment>
        <TopBar fileName={this.state.filename} btnCancel={this.props.btnCancel} />
        <FilePreview fileContent={this.state.lines} />
      </React.Fragment>
    )
  }
}

export default FrameParser
