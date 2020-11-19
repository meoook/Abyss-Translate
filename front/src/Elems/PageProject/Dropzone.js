import React, { useEffect } from "react"

const Dropzone = ({ addFiles, disabled, isSolo = false }) => {
  useEffect(() => {
    if (!isSolo) {
      console.log(`SOLO IS ${isSolo} set multy`)
      fileSelector.setAttribute("multiple", "multiple")
    } else {
      fileSelector.removeAttribute("multiple")
    }
    // eslint-disable-next-line
  }, [isSolo])

  const onFileAdded = (event) => {
    if (disabled) return
    addFiles([...event.target.files])
    event.target.value = "" // Reset input file
  }
  const fileSelector = document.createElement("input")
  fileSelector.setAttribute("type", "file")
  fileSelector.addEventListener("change", onFileAdded)

  const onFileDropped = (event) => {
    event.preventDefault()
    event.stopPropagation()
    if (disabled) return
    event.target.classList.remove("highlight")
    addFiles([...event.dataTransfer.files])
    event.target.value = "" // Reset input file
  }

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
      // disabled={disabled}
      className={`dropzone${disabled ? " disable" : ""}`}
      onClick={openFileDialog}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onFileDropped}
      style={{ backgroundImage: "url(/add_circle_out.svg)" }} // is it ok ?
    >
      Нажми или перетащи файл{!isSolo ? "ы" : ""} в область для добавления
    </div>
  )
}

export default Dropzone
