1. Left Sidebar (Job Announcements):
Would you like to keep the "New Job +" button in the current position?
- I updated the design please take a look <|> screenshot_5 <|>
Should each job announcement item show the number of sections?
- no we sow the date instead of the announcement and the company, the title sould be the first markdown header section
What should happen when clicking the red trash icon?
- its ok the ways we have it gight now
Should we implement drag-and-drop functionality for reordering?
- no but we need a search bar to search for companies which will also be in our contacts database

2. Main Editor Area:
The title shows "Job Anouncement" - should we fix this typo?
- yes
I see tags like "Sidebar", "erfüllt", "Bedienung" - are these predefined categories or user-created?
Should the editor support rich text formatting?
How should the tag system work within the editor - can users add tags inline?

3. Right Sidebar (Highlights):
Should the search bar at the top filter both highlights and tags?
- no only content of highlights
I notice timestamps (e.g., "5 December 2024") - what information should be tracked for each highlight?
- the date it got updated
How should highlights be grouped - by tag, by date, or both?
- the order depends on where thy are in the text of the Main Editor area
Should users be able to edit/delete highlights directly from this panel?
- on hover we show the highlight-selection-toolbar i will add <|> screenshot_1 <|>
- this is the same menu we show when we select a highlight in the text
- we differenctiate between selected text with no highlight and seelecting a highlight containing text

4. Tag System:
What colors should be used for different tag types?
- random new that was not used before
- useres can change the color when we hover over a tag we show the Tag Editing Toolbar <|> screenshot_2 <|>
Should tags be hierarchical (parent-child relationships)?
- tags live on a Tags bord page <|> screenshot_3 <|>
- tags are associated to a highlight (small number incator in the tags)
Do you want to limit the number of tags that can be applied to a selection)?
- no there is no limit on the number of tags that can be applied to a highlight
Should there be a way to manage/edit tags globally?
- yes the Tags Page <|> screenshot_3 <|>

5. UI/UX Elements:
Should we keep the "Share" and "Editable" buttons in the top bar?
- we will not use the "Share" button for now
- we will keep the "Editable" button
Do you want keyboard shortcuts for common actions?
- please prapare a json config where we will define shortcuts for every action later
Should we add a way to collapse/expand the sidebars?
- yes and we go with the simplest solution
How should the responsive design work on smaller screens?
- the Tags Collection Area will look differenct moer compressed <|> screenshot_4 <|>

please ask me for the screenshots now one by one to better understand my awnsers
