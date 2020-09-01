import React from "react"

// App images
import ImgDesert from "../IMG/images/desert.jpg"
import ImgSnow from "../IMG/images/snow.jpg"
import ImgEmpty from "../IMG/images/empty.jpg"
import ImgExtensions from "../IMG/images/extensions.jpg"
import ImgExtensions2 from "../IMG/images/extensions2.png"

export const DisplayImage = ({ name }) => {
  switch (name) {
    case "extensions":
      return <img src={ImgExtensions} alt='extensions' />
    case "extensions2":
      return <img src={ImgExtensions2} alt='extensions' />
    case "desert":
      return <img src={ImgDesert} alt='desert' />
    case "snow":
      return <img src={ImgSnow} alt='snow' />
    default:
      return <img src={ImgEmpty} alt='' />
  }
}
