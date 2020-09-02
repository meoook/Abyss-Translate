import React, { useEffect, useContext, useState } from 'react';
import { useParams } from 'react-router-dom';
import AppContext from '../../context/application/appContext';
import TranslateMenu from './TranslateMenu';
import TranslateMark from './TranslateMark';
import Paginator from '../AppComponents/Paginator';
import Loader from '../AppComponents/Loader';
import { DisplayImage } from '../images';

const PageTranslateFile = (props) => {
  // STATE
  const { id } = useParams();
  const { transMarkList, transFileInfo, translates } = useContext(AppContext);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(25);
  const [same, setSame] = useState(false);
  const [noSame, setNoSame] = useState(false);
  const [like, setLike] = useState(false);
  const [noTrans, setNoTrans] = useState(0);
  const [langOrig, setLangOrig] = useState(null);
  const [langTrans, setLangTrans] = useState(null);
  const [activeMark, setActiveMark] = useState(null);

  useEffect(() => {
    transFileInfo(id, page, size, same, noTrans); // TODO: make like Promise
    // eslint-disable-next-line
  }, [id]);

  useEffect(() => {
    if (!translates.lang_orig) return;
    if (!langOrig) setLangOrig(translates.lang_orig);
    if (!langTrans && translates.translated_set.length)
      setLangTrans(translates.translated_set[0].language);
    setLoading(false);
  }, [translates, langOrig, langTrans]);

  const fixPageNumber = (p, s, count) =>
    p * s > count ? Math.ceil(count / s) : p;

  const refreshPage = (pageNumber, pageSize) => {
    const fixedNumber = fixPageNumber(pageNumber, pageSize, translates.count);
    setLoading(true);
    setPage(fixedNumber);
    setSize(pageSize);
    transMarkList(id, fixedNumber, pageSize, same, noTrans).then(() => {
      setLoading(false);
    });
  };
  const changeSame = () => {
    transMarkList(id, page, size, !noSame, noTrans);
    setNoSame(!noSame);
  };
  const changeNoTrans = () => {
    let val = noTrans ? 0 : langTrans;
    transMarkList(id, page, size, same, val);
    setNoTrans(val);
  };

  return (
    <div className='container-fluid'>
      {loading ? (
        <Loader />
      ) : (
        <>
          <div className='row justify bottom'>
            <div className='row center'>
              <div className='card card-image-small'>
                <DisplayImage name='extensions2' />
              </div>
              <h1 className='t-big ph-2'>{translates.name}</h1>
            </div>
            <div className='card p-1'>
              <div className='row center'>
                <div className='mh-2 col'>элементов</div>
                <div className='mh-2 col col-3'>{translates.items}</div>
              </div>
              <div className='row center mt-2'>
                <div className='mh-2 col'>слов</div>
                <div className='mh-2 col col-3'>{translates.words}</div>
              </div>
            </div>
          </div>
          <hr />
          <TranslateMenu
            langOrig={langOrig}
            setLangOrig={setLangOrig}
            langTrans={langTrans}
            setLangTrans={setLangTrans}
            same={same}
            setSame={setSame}
            noSame={noSame}
            setNoSame={changeSame}
            like={like}
            setLike={setLike}
            noTrans={noTrans}
            setNoTrans={changeNoTrans}
          />
          <div className='expl row'>
            <div className='col col-7 column'>
              <div className='table-head ml-3'>
                <div className='col col-3'>Название</div>
                <div className='col col-2'>Позиций</div>
                <div className='col col-2'>Слов</div>
                <div className='col col-3'>Прогресс перевода</div>
                <div className='col col-2'>GIT статус</div>
              </div>
              <div
                className={`scroll-y${
                  translates.count / size > 1 ? ' paginate' : ''
                }`}>
                {!translates.results ? (
                  <div>NO ITEMS</div>
                ) : (
                  translates.results.map((mark) => (
                    <TranslateMark
                      key={mark.id}
                      mark={mark}
                      langOrig={langOrig}
                      langTrans={langTrans}
                      same={same}
                      setActive={setActiveMark}
                    />
                  ))
                )}
              </div>
              {translates.count / size > 1 && (
                <Paginator
                  page={page}
                  size={size}
                  total={translates.count}
                  refresh={refreshPage}
                />
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default PageTranslateFile;
