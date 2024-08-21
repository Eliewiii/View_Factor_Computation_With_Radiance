
sur_1.rad contains the emitter surface.
sur_3.rad contains the receiver surface.
sur_2.rad contains the receiver and a surface in the middle of the emitter and receiver taht block all rays.

### Run the following command to generate the oct file
```bash
oconv path/to/sur_2.rad > path/to/sur_2.oct
```

### Run the following command to compute the view factor without the context
```bash
rfluxmtx -h- -ab 0 -c 1000  "!xform -I "path/to/sur_1.rad"" path/to/sur_3.rad > path/to/out.txt
```
The value should be higher than 0

### Run the following command to compute the view factor with the context
```bash
rfluxmtx -h- -ab 0 -c 1000  "!xform -I "path/to/sur_1.rad"" path/to/sur_3.rad -i path/to/sur_2.oct > path/to/out.txt
```
The value should be 0
```