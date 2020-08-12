import React from "react"

export default function UserFiles({ files, openLoadFiles }) {
  return (
    <div>
      <div className='row title'>
        <h1>Мои файлы для перевода</h1>
        <div>
          <button className='btn green' value='options' onClick={openLoadFiles}>
            Загрузить
          </button>
        </div>
      </div>
      <div className='my-table'>
        <table>
          <thead>
            <tr>
              <td>&nbsp;</td>
              <td>Load time</td>
              <td>Translate start</td>
              <td>Filename</td>
              <td>Total words</td>
              <td>Words translated</td>
              <td>Words left</td>
            </tr>
          </thead>
          <tbody>
            {files.map((file, index) => {
              return (
                <tr key={file.id} className={file.phase}>
                  <td>{index + 1}</td>
                  <td>{file.timeLoaded}</td>
                  <td>{file.timeActiveEnd}</td>
                  <td>{file.name}</td>
                  <td>{file.wordsTotal}</td>
                  <td>{file.wordsTranslated}</td>
                  <td>{file.wordsLeft}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
