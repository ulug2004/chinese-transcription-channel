# docs\edit — the author's working copies

Two files here, and only these two, are for editing by hand:

    paper_EDIT.docx            the submission, 16 pages
    supplement_S1_EDIT.docx    Supplementary S1, all 40 rows

Nothing in the build pipeline writes to this folder, so edits made here
cannot be overwritten by a rebuild.

## Procedure

1. Edit either file in LibreOffice Writer. On save, choose
   "Use Word 2007-365!" so it stays .docx.
   Track changes (Ctrl+Shift+C) is optional but makes the fold-back
   easier to verify.

2. Close the file. An open document leaves a .~lock file and a later
   save from that window can overwrite a newer version.

3. Say that the edits are ready. Claude folds the wording back into the
   masters and rebuilds the PDF, DOCX and HTML in docs\ from them.

4. Claude then replaces the two files here with fresh copies of the
   rebuilt documents, so this folder never drifts behind docs\.

## Masters, for reference

The documents in docs\ are generated. Do not edit them; they are
overwritten on every rebuild.

    paper                  docsrc\paper.html          -> build_paper.py, topdf.py
    supplement, prose      docsrc\s1_prose_top.html
                           docsrc\s1_prose_bottom.html
    supplement, 40 rows    docsrc\s1_rows.py          -> build_s1.py
    process notes          docsrc\plain.html          (not submitted)

## Division of labour while editing is in progress

Prose is the author's. Claude does not touch docsrc\paper.html unless
asked, so the two versions cannot diverge.

Structural changes stay with Claude: renumbering tables, adding or
reordering references, moving sections, cross-references. Ask, and a
fresh EDIT copy follows, rather than fighting Word's numbering by hand.
