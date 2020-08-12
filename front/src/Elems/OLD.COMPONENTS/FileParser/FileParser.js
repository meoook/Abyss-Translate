import React from "react"
import FrameInput from "./FrameInput"
import FrameParser from "./FrameParser"

class FrameMain extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      file: null,
      fileLoaded: false,
      hide: false,
    }
  }

  fileReturn = (file) => {
    this.setState({ hide: true })
    setTimeout(() => {
      this.setState({ file: file, fileLoaded: true, hide: false })
    }, 2500)
  }

  fileCancel = () => {
    this.setState({ file: null, hide: true })
    setTimeout(() => {
      this.setState({ fileLoaded: false, hide: false })
    }, 800)
  }

  render() {
    let content
    if (this.state.fileLoaded) {
      content = <FrameParser file={this.state.file} btnCancel={this.fileCancel} />
    } else {
      content = <FrameInput onLoaded={this.fileReturn} />
    }
    return (
      <React.Fragment>
        <h1>Import Files</h1>
        <div className={!this.state.hide ? "file-work-frame" : "file-work-frame disabled"}>{content}</div>
      </React.Fragment>
    )
  }
}

export default FrameMain
