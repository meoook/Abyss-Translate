import React from "react"

class TopBar extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      fileLoaded: false,
      fileName: props.fileName || "No file chosen",
      fileNameDb: props.fileName.match(/(.*)\..{1,4}$/)[1] || "",
      code: "utf8",
      method: "repeat",
    }

    this.handleChangeFile = this.handleChangeFile.bind(this)
    this.handleChangeFileDb = this.handleChangeFileDb.bind(this)
    this.handleChangeCode = this.handleChangeCode.bind(this)
    this.handleChangeLang = this.handleChangeLang.bind(this)
    this.handleChangeMethod = this.handleChangeMethod.bind(this)
  }

  handleChangeFile(event) {
    this.setState({ fileName: event.target.value })
  }

  handleChangeFileDb(event) {
    this.setState({ fileNameDb: event.target.value })
  }

  handleChangeCode(event) {
    this.setState({ code: event.target.value })
  }

  handleChangeLang(event) {
    this.setState({ method: event.target.value })
  }

  handleChangeMethod(event) {
    this.setState({ method: event.target.value })
  }

  render() {
    return (
      <table className='file-work-frame-topbar'>
        <tbody>
          <tr>
            <td rowSpan='2' className='file-name'>
              {this.props.fileName}
            </td>
            <td>Название в DB</td>
            <td>Кодировка</td>
            <td>Язык оригинала</td>
            <td>Метод</td>
            <td rowSpan='2' className='file-setted'>
              Подтвердить
            </td>
            <td rowSpan='2' className='file-cancel' onClick={this.props.btnCancel}>
              Отмена
            </td>
          </tr>
          <tr>
            <td className='input'>
              <input type='text' placeholder='DB filename' defaultValue={this.state.fileNameDb} />
            </td>
            <td className='input'>
              <select value={this.state.code} onChange={this.handleChangeCode}>
                <option value='ANSI'>ANSI</option>
                <option value='utf8'>UTF-8</option>
                <option value='utf8-sig'>UTF-8-BOM</option>
                <option value='utf16'>UTF-16</option>
                <option value='utf16-sig'>UTF-16-BOM</option>
              </select>
            </td>
            <td className='input'>
              <select value={this.state.lang} onChange={this.handleChangeLang}>
                <option value='ru'>Russian</option>
                <option value='en'>Eanglish</option>
                <option value='de'>Deutch</option>
              </select>
            </td>
            <td className='input'>
              <select value={this.state.method} onChange={this.handleChangeMethod}>
                <option value='repeat-r'>Repeat rows</option>
                <option value='repeat-l'>Repeat lines</option>
                <option value='replace'>Replace</option>
              </select>
            </td>
          </tr>
        </tbody>
      </table>
    )
  }
}

export default TopBar
