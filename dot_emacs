(defadvice comint-simple-send (around allow_clear_command activate)
  "If the input is the word \"clear\", erase buffer."
  (if (string-equal "clear" string)
      (progn
        (kill-word -1)
        (forward-line 0)
        (delete-region 1 (point))
        (end-of-buffer))
    ad-do-it))


(global-set-key "\C-xg" 'goto-line)
(global-set-key [f1] 'shell)
(global-set-key [f2] 'compile)
(global-set-key [f3] 'gdb)

(defun toggle-selective-display-column ()
  "set selective display fold everything greater than the current column, or toggle off if active"
  (interactive)
  (set-selective-display
   (if selective-display nil (or (+ (current-column) 1) 1))))

(global-set-key [f4] 'toggle-selective-display-column)



;; (set-default-font "lucidasanstypewriter-12")
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
