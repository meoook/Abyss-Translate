import React from "react"

const UserStats = ({ stats }) => {
  return (
    <table className='table-nobd user-stats'>
      <thead>
        <tr>
          <td>&nbsp;</td>
          <td>RU</td>
          <td>EN</td>
          <td>DE</td>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Uploaded files</td>
          <td>{stats.filesUploaded.ru}</td>
          <td>{stats.filesUploaded.en}</td>
          <td>{stats.filesUploaded.de}</td>
        </tr>
        <tr>
          <td>Translated files</td>
          <td>{stats.filesTranslated.ru}</td>
          <td>{stats.filesTranslated.en}</td>
          <td>{stats.filesTranslated.de}</td>
        </tr>
        <tr>
          <td>Translated words</td>
          <td>{stats.wordsTranslated.ru}</td>
          <td>{stats.wordsTranslated.en}</td>
          <td>{stats.wordsTranslated.de}</td>
        </tr>
        <tr>
          <td>Aproved translates</td>
          <td>{stats.wordsTranslatedAproved.ru}</td>
          <td>{stats.wordsTranslatedAproved.en}</td>
          <td>{stats.wordsTranslatedAproved.de}</td>
        </tr>
        <tr>
          <td>Error translates</td>
          <td>{stats.wordsTranslatedErrors.ru}</td>
          <td>{stats.wordsTranslatedErrors.en}</td>
          <td>{stats.wordsTranslatedErrors.de}</td>
        </tr>
      </tbody>
    </table>
  )
}

export default UserStats
