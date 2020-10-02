export const displayStringDate = (stringDate) => {
  const date = new Date(stringDate)
  const checkLen = (strOrInt) => {
    if (+strOrInt >= 10) return `${strOrInt}`
    return `0${strOrInt}`
  }
  return `${checkLen(date.getDate())}.${checkLen(date.getMonth() + 1)}.${date.getFullYear()}`
}

export const findIconChars = (stringVal = "") => {
  let iconChars = stringVal.match(/[A-ZА-Я]/g)
  if (iconChars && iconChars.length > 1) {
    iconChars = iconChars.join("").substring(0, 2)
  } else if (stringVal.includes(" ")) {
    iconChars = stringVal.split(" ").reduce((shortName, namePart) => {
      return `${shortName}${namePart.charAt(0)}`.substring(0, 2)
    }, "")
  } else {
    iconChars = stringVal.substring(0, 2)
  }
  return iconChars.toUpperCase()
}

export const textCutByLen = (text, maxLen) => (text.length < maxLen ? text : `${text.slice(0, maxLen)}...`)
