import React from "react"

const Dropzone = ({ addFiles, disabled }) => {
  const onFileAdded = (event) => {
    if (disabled) return
    addFiles([...event.target.files])
    event.target.value = "" // Reset input file
  }

  const onFileDropped = (event) => {
    event.preventDefault()
    event.stopPropagation()
    if (disabled) return
    event.target.classList.remove("highlight")
    addFiles([...event.dataTransfer.files])
    event.target.value = "" // Reset input file
  }

  const fileSelector = document.createElement("input")
  fileSelector.setAttribute("type", "file")
  fileSelector.addEventListener("change", onFileAdded)
  fileSelector.setAttribute("multiple", "multiple")

  const openFileDialog = (event) => {
    if (disabled) return
    fileSelector.click()
  }

  const onDragOver = (event) => {
    event.preventDefault()
    event.stopPropagation()
    if (disabled) return
    event.target.classList.add("highlight")
  }

  const onDragLeave = (event) => {
    if (disabled) return
    event.target.classList.remove("highlight")
  }

  return (
    <div
      style={{ cursor: disabled ? "default" : "pointer" }}
      className={`dropzone${disabled ? " disable" : ""}`}
      onClick={openFileDialog}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onFileDropped}>
      Click here to select files
      <br />
      Or drop files in this area
    </div>
  )
}

export default Dropzone
