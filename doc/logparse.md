# LogParse
## Purpose
This project is used to generate release notes for different customers from a single master file.

## How it works
### File format
The user must create a master file using the markdown format, however a limited number of syntaxes are supported:
- Release entries should always start with `#` and end with `\n`
- Text entries start with `[a-zA-Z]` and end with `\n\n` or `\n-` `\n -` etc...
- Log entries always start with `-` and end with `\n\n` or `\n-` `\n -` etc...

**Example of correct release notes:**
```md
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

## x.y.z (unreleased)
- Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi

## 0.5.0 (01-01-2020)
- [Foo][All]Lorem ipsum dolor sit amet
- [Bar]Consectetuer adipiscing elit

## 0.4.0 (01-01-2020)
- [Foo]Aenean commodo ligula eget dolor

## 0.3.0 (01-01-2020)
- Aenean massa

## 0.2.0 (01-01-2020)
- Cum sociis natoque penatibus et magnis dis parturient montes
- nascetur ridiculus mus. Donec quam felis

## 0.1.0 (01-01-2020)
- [Foo]Aenean imperdiet.
```

#### Multiple line entries
Using markdown syntax it is possible to write a log entry on multiple lines.

```md
## 0.5.0 (01-01-2020)
- [Foo]This entry
is correctly
labeled `foo`

This is a different entry.
```

#### Sub-list of entries
When using a chained list of entries, the label need to be re-applied on each line.

```md
## 0.5.0 (01-01-2020)
- [Foo]This entry is correctly labeled `foo`
  - [Foo]This entry is correctly labeled `foo`
  - This entry is NOT labeled `foo`
```

### Labels
To generate customer release notes the user must add labels such as `[foo]` `[bar]` `[all]` ito the master file of the project.
These labels are used to generate customer release notes that only include a subset of labels.

**Example of master release notes:**
```md
## x.y.z (unreleased)
- Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi

## 0.5.0 (01-01-2020)
- [All]Cum sociis natoque penatibus et magnis dis parturient montes
- [Foo]Lorem ipsum dolor sit amet
- [Bar]Consectetuer adipiscing elit
```

**Example of output for label `foo`:**
```md
## 0.5.0 (01-01-2020)
- Cum sociis natoque penatibus et magnis dis parturient montes
- Lorem ipsum dolor sit amet
```

Other rules to be aware of:
- Labels are not case sensitive and should only contain letters or `_`. `Foo` `foo` `fOo` all represent the same label.
- `All` is a special label which ensures the entry is always included in any generated output.
- Labels should only be added to the log entries of the release notes, and NOT to the release entries.
- Empty release entries are discarded from the output. For instance if all the log entries have been filtered out.

## Command-line interface
When installing the python package a CLI `logparse` will also be installed on the machine. This utility can be used to perform most of the actions from command-line.

### Render all content
This command generates a release note containing all the entries from the master file. The resulting file is similar to the inputs but all the labels removed have 

```
logparse render --input "./RELEASE_NOTES_MASTER.md" --output "./RELEASE_NOTES.md"
```

### Render specific labels
This command generates a release note containing only the entries marked by one or several specified labels.

```
logparse render --input "./RELEASE_NOTES_MASTER.md" --output "./RELEASE_NOTES.md" --labels foo bar
```

### Check a release entry is present
This function can be used to check that the user did not forget to update the release notes before making a tag.
The command returns "0" if the specified tag was found or "1" otherwise, so this can be integrated directly from a CI release script.

```
logparse find_tag --input "./RELEASE_NOTES_MASTER.md" --tag 1.2.3
```
