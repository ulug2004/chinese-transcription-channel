# docs\edit, the author's working copies

Two files here, and only these two, are for editing by hand:

    paper_EDIT.docx            the submission, 16 pages
    supplement_S1_EDIT.docx    Supplementary S1, all 40 rows

**Read this before editing.** The claim that once stood here, that nothing in
the build pipeline writes to this folder, was not true in practice. The build
regenerates both files at the end of every run and Claude then copies them
here, so an edit made here IS overwritten by the next rebuild unless it has
been folded into the masters first.

The guard is `docsrc\check_edits.py`. Every build now writes
`edit_fingerprint.json` beside these two files, recording the SHA-256 of each
copy as shipped. Before any rebuild, Claude stages the three files out of this
folder and runs `check_edits.py` against them: an unchanged fingerprint means
the copies are still ours and the build may proceed, a changed one means the
author has edited and the rebuild must wait until the wording is folded into
`docsrc\`. Do not delete `edit_fingerprint.json`; without it the check cannot
tell an edit from an untouched copy and Claude has to ask.

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
