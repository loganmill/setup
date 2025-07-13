;; stuck minifuffer fix:
;; (set-window-buffer (minibuffer-window) (get-buffer " *Minibuf-0*"))
(setq vc-make-backup-files t)

;; (setq shell-command-switch "-ic")

 (defadvice comint-simple-send (around allow_clear_command activate)
   "If the input is the word \"clear\", erase buffer."
   (if (string-equal "clear" string)
       (progn
         (kill-word -1)
         (forward-line 0)
         (delete-region 1 (point))
         (goto-char (point-max)))
     ad-do-it))


(push (cons "\\*shell\\*" display-buffer--same-window-action) display-buffer-alist)

 (defun alt-shell-dwim (arg)
   "Run an inferior shell like `shell'. If an inferior shell as its I/O
 through the current buffer, then pop the next buffer in `buffer-list'
 whose name is generated from the string \"*shell*\". When called with
 an argument, start a new inferior shell whose I/O will go to a buffer
 named after the string \"*shell*\" using `generate-new-buffer-name'."
   (interactive "P")
   (let* ((shell-buffer-list
 	  (let (blist)
	     (dolist (buff (buffer-list) blist)
	       (when (string-match "^\\*shell\\*" (buffer-name buff))
	 	(setq blist (cons buff blist))))))
	  (name (if arg
	 	   (generate-new-buffer-name "*shell*")
	 	 (car shell-buffer-list))))
     (shell name)))

(global-set-key [f3] 'gdb)

(defun toggle-selective-display-column ()
  "set selective display fold everything greater than the current column, or toggle off if active"
  (interactive)
  (set-selective-display
   (if selective-display nil (or (+ (current-column) 1) 1))))

(require 'indent-bars)
(global-set-key [f1] 'alt-shell-dwim)
(global-set-key [f2] 'compile)
(global-set-key [f4] 'revert-buffer)
(global-set-key [f5] 'toggle-selective-display-column)

(global-set-key [f6] 'indent-bars-mode)
(global-set-key [f7] 'rotate-window)

(setq-default tab-width 2 indent-tabs-mode nil)
(server-start)
(setq c-indent-mode nil)

(cond ((fboundp 'global-font-lock-mode)
       ;; Turn on font-lock in all modes that support it
       (global-font-lock-mode t)
       ;; Maximum colors
       (setq font-lock-maximum-decoration t)))

(setq font-lock-keyword-face 'font-lock-constant-face)
(setq font-lock-variable-name-face 'font-lock-comment-face)


(c-add-style
 "grd-style"
 '("stroustrup"       ; style to inherit from. There are many others
   (indent-tabs-mode . nil) ; use spaces rather than tabs
   (c-basic-offset . 2)     ; indent by four spaces
   (tab-width . 4)          ; if the file specifies tabs, make them 4 chars wide
   (c-tab-always-indent . 1) ; tabs when in literals & comments,
indent otherwise
   (c-offsets-alist . ; custom indentation rules
                      ((inline-open . 0)
                       (brace-list-open . 0)
                       (statement-case-open . +)))))

(add-hook 'c++-mode-hook
          (lambda () (c-set-style "grd-style")))

(add-hook 'shell-mode-hook 
          'ansi-color-for-comint-mode-on)

(setq ansi-color-names-vector
   ["black" "red" "green" "orange" "PaleBlue" "magenta" "cyan" "white"])


 (defun try-to-add-imenu ()
  (condition-case nil (imenu-add-to-menubar "Nav") (error nil)))
 (add-hook 'font-lock-mode-hook 'try-to-add-imenu)

(global-set-key [C-tab] 'other-window)

;;  '(initial-buffer-choice "/home/gdiener/.bashrc")
(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(c-basic-offset 2)
 '(c-offsets-alist '((substatement-open . +) (case-label . 0)))
 '(column-highlight-mode nil)
 '(custom-safe-themes
   '("388132d2660c2eb59ba12e9325998bdc3d0e246b2c5df431b1b57e8dca57f611"
     "e525bee43b813bbf51ecf4ce8594fc93f625aa86f239537819564cb82e8499cd"
     "f6dbbd5601809d772cfce9b8848b48eba1cf2350b1871aa971e20c313c4c9a51"
     "bcdfdbfed67dd99d6c17475b8dde3f8e575fb9741252c6ac18ed44f42d20eb52"
     default))
 '(debug-on-error t)
 '(electric-indent-mode nil)
 '(inhibit-startup-screen t)
 '(js2-include-jslint-globals nil)
 '(js2-mode-show-strict-warnings t)
 '(large-file-warning-threshold nil)
 '(make-backup-files nil)
 '(mouse-wheel-progressive-speed nil)
 '(org-babel-load-languages '((python . t)))
 '(org-babel-python-command "python3")
 '(org-log-done t)
 '(package-archives '(("gnu" . "http://elpa.gnu.org/packages/")))
 '(package-selected-packages
   '(aider aidermacs alect-themes anti-zenburn-theme atomic-chrome
           claude-code eat eink-theme flycheck flymake-easy
           flymake-jslint htmlize indent-bars indent-guide
           js-auto-format-mode js-format js2-mode js2-refactor magit
           pdf-tools prettier-js rotate smartparens transient-cycles
           vline vterm w3m web-mode xref-js2))
 '(package-vc-selected-packages
   '((claude-code :url "https://github.com/stevemolitor/claude-code.el")))
 '(perl-indent-level 2)
 '(prettier-js-width-mode nil)
 '(revert-without-query '(".*"))
 '(scroll-conservatively 1)
 '(scroll-preserve-screen-position t)
 '(sh-basic-offset 2)
 '(tags-revert-without-query t))
;;(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
;; '(default ((t (:family "DejaVu Sans Mono" :foundry "PfEd" :slant normal :weight normal :height 151 :width normal))))

;;(package-initialize)
;;(eide-start)
(load-theme `manoj-dark t)
;;(load-theme `dichromacy t)
;;(load-theme `misterioso t)
;;(load-theme `leuven t)
(setq explicit-shell-file-name "/bin/bash")
(windmove-default-keybindings)
(set-cursor-color "#ffffff")

(defun match-paren (arg)
  "Go to the matching paren if on a paren; otherwise insert %."
  (interactive "p")
  (cond ((looking-at "\\s\(") (forward-list 1) (backward-char 1))
        ((looking-at "\\s\)") (forward-char 1) (backward-list 1))
        (t (self-insert-command (or arg 1)))))


(require 'package)
(add-to-list 'package-archives
             '("melpa-stable" . "http://stable.melpa.org/packages/") t)
(add-to-list 'package-archives
             '("melpa" . "http://melpa.org/packages/") t)
(add-to-list 'package-archives
             '("gnu" . "https://elpa.gnu.org/packages/") t)
(package-initialize)
(when (not package-archive-contents)
  (package-refresh-contents))


(global-set-key (kbd "C-x g") 'magit-status)

(require 'org)
(define-key global-map "\C-cl" 'org-store-link)
(define-key global-map "\C-ca" 'org-agenda)
(setq org-log-done t)

(require 'atomic-chrome)
(atomic-chrome-start-server)

(org-babel-do-load-languages
 'org-babel-load-languages
 '((python . t)))
(setq org-confirm-babel-evaluate nil)


(require 'web-mode)
 (add-to-list 'auto-mode-alist '("\\.html?\\'" . web-mode))


(require 'js2-mode)
 (add-to-list 'auto-mode-alist '("\\.js\\'" . js2-mode))

;; Better imenu
(add-hook 'js2-mode-hook #'js2-imenu-extras-mode)

;; (require 'js2-refactor)
;; (require 'xref-js2)

 (add-hook 'js2-mode-hook (lambda ()
   (add-hook 'xref-backend-functions #'xref-js2-xref-backend nil t)))

(require 'prettier-js)
 (add-hook 'js2-mode-hook 'prettier-js-mode)
 (add-hook 'web-mode-hook 'prettier-js-mode)


;;(require 'flymake-jslint)
;;(add-hook 'js-mode-hook 'flymake-jslint-load)

(require 'json)
(require 'flycheck)

(setq visible-bell 1)

;; rebind C-k as js2 highjacks it
(global-set-key (kbd "C-k") 'kill-line)


(when (find-font (font-spec :family "Iosevka Term"))
 (set-face-attribute 'default nil :font "Iosevka Term-16"))


;; (require 'indent-guide)




 (defun pretty (posBegin posEnd)
  "Run prettier on current region."
  (interactive "r")
  (message "Formatting …")
  (let* (
         (old-prettier-args prettier-js-args)
         (prettier-js-args (append old-prettier-args 
                                                 (list "--range-start" (number-to-string posBegin) 
                                                        "--range-end" (number-to-string posEnd))))
         )
    (prettier-js)
    )
  )


;; Write backups to ~/.emacs.d/backup/
;;(setq backup-directory-alist '(("." . "/home/grd/.emacs.d/backup"))
;;      kept-old-versions      10
;; C-u C-x C-s
(setq backup-directory-alist '(("." . "~/.emacs.d/backup"))
      backup-by-copying      t 
      version-control        t
      delete-old-versions    t
      kept-new-versions      10
      make-backup-files      t
      vc-make-backup-files   t
)

(add-to-list 'package-archives
    '("nongnu" . "https://elpa.nongnu.org/nongnu/"))
(use-package claude-code :ensure t
  :vc (:url "https://github.com/stevemolitor/claude-code.el" :rev :newest)
  :config (claude-code-mode)
  :bind-keymap ("C-c c" . claude-code-command-map)) ;; or your preferred keyU


(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )
