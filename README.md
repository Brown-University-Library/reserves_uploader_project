# Purpose

Allows staff to upload PDFs for [Leganto][LG].

Avoids past issue where tens of thousands of files were deposited in a single directory, affecting server performance, by saving using a `pairtree` approach: if the filename is `1234567890.pdf`, the file will be saved to `/path/to/files/12/34/1234567890.pdf`.

[LG]: <https://exlibrisgroup.com/products/leganto-reading-list-management-system/>

---
