import React from "react"

export default function FilePreview({ fileContent }) {
  return (
    <table className='file-view'>
      <tbody>
        {fileContent.slice(0, 35).map((line, index) => {
          return (
            <tr key={index}>
              <td className='row-number'>{index + 1}</td>
              {line.split("\t").map((item, index) => (
                <td key={index}>{item}</td>
              ))}
            </tr>
          )
        })}
      </tbody>
    </table>
  )
}
